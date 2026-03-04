import json
from collections import Counter

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

# kociemba面序: U R F D L B
KOCIEMBA_FACE_ORDER = [0, 5, 2, 1, 4, 3]

# 将颜色索引映射到中心面字符
COLOR_TO_FACE_CHAR = {
    0: 'U',
    1: 'D',
    2: 'F',
    3: 'B',
    4: 'L',
    5: 'R',
}


def _get_kociemba_module():
    try:
        import kociemba
    except ImportError as exc:
        raise RuntimeError('服务端缺少 kociemba 依赖，请先执行 pip install -r requirements.txt') from exc
    return kociemba


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


def _to_kociemba_facelets(state):
    facelets = []
    for face_idx in KOCIEMBA_FACE_ORDER:
        for color_idx in state[face_idx]:
            facelets.append(COLOR_TO_FACE_CHAR[color_idx])
    return ''.join(facelets)


@csrf_exempt
@require_POST
def solve_cube(request):
    try:
        payload = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return JsonResponse({'error': '请求体必须是合法 JSON'}, status=400)

    state = payload.get('state')
    try:
        _validate_state(state)
        facelets = _to_kociemba_facelets(state)
        kociemba = _get_kociemba_module()
        solution = kociemba.solve(facelets)
    except ValueError as exc:
        return JsonResponse({'error': str(exc)}, status=400)
    except RuntimeError as exc:
        return JsonResponse({'error': str(exc)}, status=503)
    except Exception as exc:
        return JsonResponse({'error': f'求解失败: {exc}'}, status=400)

    moves = solution.split() if solution else []
    return JsonResponse({'moves': moves, 'solution': solution})
