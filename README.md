# AutoGuard Edge Capture

面向L2/L4车辆的**极简AI事件触发器与证据环形缓存**。车端不承担复杂根因诊断，只做三件事：低成本发现疑似异常、冻结事件前后数据、生成可追溯事件包。

## 核心方法

- 5Hz结构化信号流；
- 确定性安全规则负责高召回；
- PCA等价的微型线性自编码器负责识别连续行为偏离；
- 环形缓存保存异常前后窗口；
- 输出证据URI，不在车端声称“OTA导致”。

## 快速运行

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
python scripts/run_demo.py
uvicorn app:app --reload
```

API：`POST /demo`。

## 公开数据

仓库提供固定官方URL的comma2k19样例下载脚本：

```bash
python scripts/fetch_comma2k19_example.py
```

公开数据只作为真实道路信号来源；演示中的异常由受控实验生成。

## 工程边界

- 参考实现不进入车辆控制链路；
- 生产部署需按目标芯片实测P50/P95/P99延迟、内存、DDR和热负载；
- OOD、行为包络和根因诊断应在云端执行；
- 该项目不是量产安全认证组件。

详见 [SOURCES.md](SOURCES.md)。
