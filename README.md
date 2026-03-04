# 3D 魔方 + Django 后端求解

该项目现在采用 **前后端协同**：
- 前端负责 3D 魔方渲染、打乱动画、步骤展示。
- 后端（Django）提供 `POST /api/solve/` 接口，调用 `kociemba` 算法生成还原步骤。

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

> 注意：点击“自动解魔方”时，前端会把当前魔方 `state` 通过 `POST` 发送给 `/api/solve/`，后端返回 `moves` 数组，前端按返回步骤逐步还原。

## 后端接口

### `POST /api/solve/`

请求体：

```json
{
  "state": [[0,0,0,0,0,0,0,0,0], ... 共6个面]
}
```

响应体：

```json
{
  "moves": ["R", "U", "R'", "U'"],
  "solution": "R U R' U'"
}
```

## 项目结构

```text
LBL_solver/
├── index.html
├── requirements.txt
├── manage.py
├── cube_solver/
│   ├── settings.py
│   ├── urls.py
│   ├── views.py
│   └── wsgi.py
└── cube_solver_api/
    ├── urls.py
    └── views.py
```
