# 业务数据契约

班次时间为同日零点起的分钟数。assigned为原定安排、run_mode为批次实际运行方式，不能混淆。超出班次的货保留outside_shift标记。quality.final是可核对的最终抽检状态；尚未最终质量检验的货不被计为合格。基线只展示运营核对，不作试验推断。 初检selection_probability为已登记抽取机会；复检的selection_probability以已初检样本为条件。calibration为独立校验计数，不能视为判定永远正确的保证。audit_checks只核对两阶段检查原始记录，不作选择或误判校正。

## 现有组合入口

`app.inspect(data, as_of)` 是只读检查，输入为本地记录集合，输出为 JSON 可表示的字典；不修改输入。领域接口会对不符合业务口径的数据抛出 `ValueError`。缺失、不足和不适用不应伪装成零数量。
