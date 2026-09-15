# BoundLab

Python 多智能体实验项目。每个 agent 只能写自己的目录，交叉信息走消息总线，避免并行开发时互相覆盖。

不依赖 API Key 就能跑。`OPENAI_API_KEY` 可选，给 `OpenAIBrain` 用。

## 布局

```
boundlab/
  territories.yaml          # 唯一所有权表，两个 agent 不能 own 同一路径
  src/boundlab/
    guard.py                # 写保护
    bus.py                  # 消息总线
    orchestrator.py         # 串行 / 并行调度
    agents/                 # 在这里加新 agent
    tools/                  # 在这里加工具
    llm/                    # EchoBrain / OpenAIBrain
  examples/my_agent.py      # 新 agent 模板
  tests/
```

## 安装

```bash
cd boundlab
python -m pip install -e ".[dev]"
```

## 命令

```bash
python -m boundlab agents
python -m boundlab check --agent writer --path workspace/researcher/findings.md --mode write
python -m boundlab run "并行开发如何避免覆盖"
python -m boundlab run "同一目标并行" --parallel --agents researcher,writer
```

默认流水线：`researcher → writer → reviewer → coordinator`。

- researcher 只写 `workspace/researcher/`
- writer 只写 `workspace/writer/`，可读 researcher
- reviewer 只写 `workspace/reviewer/`
- coordinator 只写 `shared/` 和 `inbox/`

产物在 `var/run/`。

## 加一个 agent

1. 仿 `examples/my_agent.py` 写类，放到 `src/boundlab/agents/`
2. 在 `territories.yaml` 增加同名条目，`owns` 不要和别人重叠
3. 在 `src/boundlab/agents/registry.py` 注册
4. `python -m boundlab run "..." --agents your_name`

不要改别人 `owns` 里的文件。要给下游看内容，用 `ctx.publish(...)`。

## 测试

```bash
cd boundlab
python -m pytest
```
