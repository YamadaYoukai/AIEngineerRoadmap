# Click MCP Client 端到端验证

## 1. 验证目标

这是一次针对公开 Click 仓库的端到端验证：
`Client → search_code → get_file_context → evidence-based answer`。

本次验证使用名为 `code-search` 的 MCP Server。Client 先用真实错误信息定位源码，再尝试读取命中位置附近的源码，并将 Client 可观察到的请求、返回结果和最终结论保存为证据。

## 2. Client 原始请求

在公开仓库 `click` 中，根据错误信息 `The given command does not have a callback that can be invoked.` 定位 Python 源码；先调用一次 `search_code`，再根据真实命中调用一次 `get_file_context`；记录两次 MCP Tool 的完整可见返回结果，并仅根据源码上下文回答错误所在的类、方法和抛出条件；最后生成本证据文档。

## 3. Client 调用轨迹

| 顺序 | 调用方 | 动作 | 结果 |
| --- | --- | --- | --- |
| 1 | User | 提交代码定位请求 | Client 接收请求 |
| 2 | Client | 调用 `search_code` | 成功，返回 1 个精确匹配 |
| 3 | Client | 选择真实搜索命中 | 记录 `github.com/pallets/click` / `src/click/core.py` / `848` |
| 4 | Client | 调用 `get_file_context` | 失败，Tool 返回“Repository 不存在” |
| 5 | Client | 基于源码生成答案 | 源码上下文不可获取；只能报告搜索命中和上下文获取失败 |

## 4. Tool 调用一：search_code

### 请求参数

```json
{
  "query": "The given command does not have a callback that can be invoked.",
  "repo": "click",
  "lang": "python",
  "path": "src/click/core.py",
  "limit": 5,
  "literal": true
}
```

### Tool 原始返回结果

```json
{"content":[{"type":"text","text":"{\n  \"query\": \"The given command does not have a callback that can be invoked.\",\n  \"duration_ms\": 10,\n  \"matches\": [\n    {\n      \"repo\": \"github.com/pallets/click\",\n      \"path\": \"src/click/core.py\",\n      \"line\": 848,\n      \"snippet\": \"\\\"The given command does not have a callback that can be invoked.\\\"\"\n    }\n  ]\n}"}],"structuredContent":{"query":"The given command does not have a callback that can be invoked.","duration_ms":10,"matches":[{"repo":"github.com/pallets/click","path":"src/click/core.py","line":848,"snippet":"\"The given command does not have a callback that can be invoked.\""}]},"isError":false}
```

## 5. 命中选择

选中的命中字段如下：

- repo：`github.com/pallets/click`
- path：`src/click/core.py`
- line：`848`
- snippet：`"The given command does not have a callback that can be invoked."`

选择依据是：返回的 `repo` 和 `path` 与目标公开仓库及目标文件一致，且 `snippet` 完整包含目标错误文本；`line` 是第一次 Tool 返回的真实行号。

## 6. Tool 调用二：get_file_context

### 请求参数

以下参数直接取自第一次 Tool 的真实返回结果中的 `repo`、`path` 和 `line`：

```json
{
  "repository": "github.com/pallets/click",
  "file_path": "src/click/core.py",
  "line_number": 848,
  "lines_before": 12,
  "lines_after": 12
}
```

### Tool 返回结果（公开版已脱敏）

> 原始 Tool 错误中包含本机 `REPOSITORY_ROOT` 绝对路径；公开版仅将该路径前缀替换为 `[REDACTED_REPOSITORY_ROOT]`，错误类型和仓库相对路径保持不变。

```json
{"content":[{"type":"text","text":"Error executing tool get_file_context: 读取文件上下文失败：Repository 不存在: [REDACTED_REPOSITORY_ROOT]/github.com/pallets/click"}],"isError":true}
```

## 7. Client 最终回答

`search_code` 的精确命中位于公开仓库 `click` 的 `src/click/core.py:848`（Tool 返回的 repo 为 `github.com/pallets/click`），命中行包含目标错误文本。

由于 `get_file_context` 返回 `Repository 不存在`，当前 Client 未获得该行附近的源码上下文。因此，错误所在的类、方法以及抛出条件均不可从 `get_file_context` 返回结果确认；不能据此补充结论。

## 8. 闭环验证

- `get_file_context.repository` 等于 `search_code` 返回的 `repo`：`github.com/pallets/click`。
- `get_file_context.file_path` 等于 `search_code` 返回的 `path`：`src/click/core.py`。
- `get_file_context.line_number` 等于 `search_code` 返回的 `line`：`848`。
- `search_code` 的返回结果包含目标错误文本；`get_file_context` 未返回源码上下文，因而无法再次核对上下文中的错误文本。
- 全过程只使用公开的 Click 仓库目标：`click` / `github.com/pallets/click`。
- 未记录公司仓库、公司域名、内部日志或 API Key；公开版已脱敏 Tool 错误中的本地绝对路径前缀。

## 9. 限制

- 失败根因（由用户确认）：GitHub 仓库索引前未执行 `git config zoekt.name` 并将其设置为实际本地目录名，导致 Zoekt 仓库名未与 `REPOSITORY_ROOT` 下的路径一致；该配置问题已修复。
- `get_file_context` 返回 `Repository 不存在`，因此类名、方法名、抛出条件、源码起止行、文件总行数和截断状态均不可获取。
- `search_code` 的 `duration_ms` 为 Tool 实际返回的 `10`；`get_file_context` 的耗时不可获取。
- 请求 ID、版本、时间戳以及其他未出现在 Client 可见返回中的元数据：不可获取。
- 本次演示未修改生产代码，也未创建 Git commit。
