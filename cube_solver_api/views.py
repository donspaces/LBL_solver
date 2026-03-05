import json
import collections
import collections.abc
from collections import Counter

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

# rubik_solver支持的解法
METHOD_MAP = {
    'beginner': 'Beginner',
    'cfop': 'CFOP',
    'kociemba': 'Kociemba',
}

# rubik_solver面序: U R F D L B
SOLVER_FACE_ORDER = [0, 5, 2, 1, 4, 3]

# 将颜色索引映射到中心面字符
COLOR_TO_FACE_CHAR = {
    0: 'U',
    1: 'D',
    2: 'F',
    3: 'B',
    4: 'L',
    5: 'R',
}


def _patch_collections_abc_aliases():
    # 从 Python 3.10 开始，collections 中的 Iterable/Mapping 等别名被移除。
    # rubik_solver 依赖链中的旧版 future/past 仍可能引用这些别名，这里统一回填。
    aliases = [
        'Iterable',
        'Mapping',
        'MutableMapping',
        'Sequence',
        'MutableSequence',
        'Set',
        'MutableSet',
        'Callable',
    ]
    for name in aliases:
        if not hasattr(collections, name) and hasattr(collections.abc, name):
            setattr(collections, name, getattr(collections.abc, name))


def _get_rubik_solver_utils():
    _patch_collections_abc_aliases()

    try:
        from rubik_solver import utils
    except ImportError as exc:
        raise RuntimeError(
            '服务端缺少或不兼容 rubik_solver 依赖，请先执行 pip install -r requirements.txt。'
        ) from exc
    return utils


def _validate_state(state):
    if not isinstance(state, list) or len(state) != 6:
        raise ValueError('state 必须是 6x9 的二维数组')

    flat_colors = []
    for face in state:
        if not isinstance(face, list) or len(face) != 9:
            raise ValueError('state 必须是 6x9 的二维数组')
        for color in face:
            if color not in COLOR_TO_FACE_CHAR:
                raise ValueError('state 中颜色索引必须在 0~5 之间')
            flat_colors.append(color)

    counts = Counter(flat_colors)
    if any(counts.get(color, 0) != 9 for color in range(6)):
        raise ValueError('魔方状态非法：每种颜色必须恰好出现 9 次')


def _validate_method(method):
    if method not in METHOD_MAP:
        allowed = ', '.join(METHOD_MAP.keys())
        raise ValueError(f'solver 必须是以下之一: {allowed}')


def _to_solver_facelets(state):
    facelets = []
    for face_idx in SOLVER_FACE_ORDER:
        for color_idx in state[face_idx]:
            facelets.append(COLOR_TO_FACE_CHAR[color_idx])
    return ''.join(facelets)


def _normalize_moves(raw_moves):
    return [str(move) for move in raw_moves]


@csrf_exempt
@require_POST
def solve_cube(request):
    try:
        payload = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return JsonResponse({'error': '请求体必须是合法 JSON'}, status=400)

    state = payload.get('state')
    method = payload.get('solver', 'kociemba')

    try:
        _validate_state(state)
        _validate_method(method)
        facelets = _to_solver_facelets(state)
        utils = _get_rubik_solver_utils()
        raw_moves = utils.solve(facelets, METHOD_MAP[method])
        moves = _normalize_moves(raw_moves)
    except ValueError as exc:
        return JsonResponse({'error': str(exc)}, status=400)
    except RuntimeError as exc:
        return JsonResponse({'error': str(exc)}, status=503)
    except Exception as exc:
        return JsonResponse({'error': f'求解失败: {exc}'}, status=400)

    return JsonResponse({'moves': moves, 'solution': ' '.join(moves), 'solver': method})
