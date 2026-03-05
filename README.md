# 3D 魔方 + Django 后端求解

该项目采用 **前后端协同**：
- 前端负责 3D 魔方渲染、打乱动画、步骤展示，并支持三种解法选择（Beginner / CFOP / Kociemba）。
- 后端（Django）提供 `POST /api/solve/` 接口，调用 `rubik_solver` 生成还原步骤。

## 运行方式

### 1) 安装依赖

```bash
pip install -r requirements.txt
```

### 2) 启动 Django 服务

```bash
python manage.py runserver 0.0.0.0:8000
```

### 3) 打开页面

直接访问：

- `http://127.0.0.1:8000/`

> 点击“自动解魔方”时，前端会把当前魔方 `state` 和 `solver` 通过 `POST` 发送给 `/api/solve/`，后端返回 `moves` 数组，前端按返回步骤逐步还原。

## 后端接口

### `POST /api/solve/`

请求体：

```json
{
  "state": [[0,0,0,0,0,0,0,0,0], "... 共6个面"],
  "solver": "beginner"
}
```

- `solver` 可选值：`beginner` / `cfop` / `kociemba`

响应体：

```json
{
  "moves": ["R", "U", "R'", "U'"],
  "solution": "R U R' U'",
  "solver": "beginner"
}
```
