# sorting-trial

分拣班次排程、实际运行和质量检验合格产出核对。

## 当前产品

这是可独立运行的本地分析应用，提供业务记录核对和确定性基线结果。各业务职责可直接作为 Python 接口调用，`app.py` 负责组合一次只读业务检查。结果可保存为 JSON，不依赖远端服务。

- `schedule.py`：班次安排与正式判断条件。
- `production.py`：实际换速和批次归属。
- `quality.py`：质量检验成熟及净合格产出。

## 运行

使用 Python 3.11.14，无需安装第三方包。

```bash
python3 -m unittest discover -s tests -v
python3 -m compileall -q .
python3 app.py demo
```

`inspect` 与 `demo` 使用相同业务入口；`--as-of` 选择已知日期，`--data` 可选本地数据文件，`--output` 可将本次业务核对结果写入文件。默认数据位于 `fixtures/data.json`，默认日期为 `2026-10-18`。这些命令仅展示当前已经存在的能力。

## 容器

`Dockerfile` 固定到 Python 基础镜像内容摘要。构建后运行不联网：

```bash
docker build -t sorting-trial:local .
docker run --rm --network none sorting-trial:local python -m unittest discover -s tests -v
docker run --rm --network none sorting-trial:local
```

## 数据与业务契约

样例记录全部为本地合成数据，不代表真实农户、市场成交或实际试验结果。日期采用 `YYYY-MM-DD`，有记录时点的条目以 `recorded_at` 表示系统已知日期；同一业务键存在多个修订时选已知范围内最新记录，同日由 `revision` 区分，`withdrawn` 表示撤回。可修改样例验证业务边界，不能将演示数据的统计方向视为真实结论。

班次时间为同日零点起的分钟数。assigned为原定安排、run_mode为批次实际运行方式，不能混淆。超出班次的货保留outside_shift标记。quality.final是可核对的最终抽检状态；尚未最终质量检验的货不被计为合格。基线只展示运营核对，不作试验推断。 初检selection_probability为已登记抽取机会；复检的selection_probability以已初检样本为条件。calibration为独立校验计数，不能视为判定永远正确的保证。audit_checks只核对两阶段检查原始记录，不作选择或误判校正。

接口细节见 `docs/contracts.md`。测试使用各自的内存副本和临时目录，不修改原始数据或依赖固定端口。
