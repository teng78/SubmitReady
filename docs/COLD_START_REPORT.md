# 冷启动验证报告

日期：2026-07-11（Asia/Shanghai）  
基线提交：`6087839`  
平台：Windows，Python 3.12.10，Codex 随附 Node 24/pnpm 11；Docker CLI 不可用。

## 方法

使用 `git archive HEAD` 导出到全新目录 `work/cold-start-20260711-010049`，不复制主工作区的虚拟环境或 `node_modules`。在副本中创建全新 `.venv`，执行后端 editable dev 安装；前端从 `pnpm-lock.yaml` 以 frozen 模式安装；随后从副本执行统一门禁和离线演示。

## 第一次尝试（失败）

目录：`work/cold-start-20260711-005839`。后端全新安装成功；前端解析并复用了 273 个锁定包，但 pnpm 以 `ERR_PNPM_IGNORED_BUILDS` 拒绝 `esbuild@0.27.7` 安装脚本。根因是 pnpm 11 的供应链策略没有接受旧式 `onlyBuiltDependencies` 声明。

修复：把 `frontend/pnpm-workspace.yaml` 改为精确的：

```yaml
allowBuilds:
  esbuild: true
```

没有允许其他依赖执行安装脚本。修复提交：`6087839`。

## 第二次尝试（通过）

重新从新提交导出全新副本，执行：

```text
python -m venv <cold>/.venv
<cold>/.venv/Scripts/python -m pip install -e <cold>/backend[dev]
pnpm install --frozen-lockfile                 # 在 frontend/，273 packages
<cold>/.venv/Scripts/python scripts/test_all.py --skip-install
<cold>/.venv/Scripts/python scripts/demo.py
```

真实结果：

- 后端 Ruff format/check：通过（23 files）；mypy strict：22 source files，无错误。
- pytest：21 passed，3.01s；1 个 Starlette/httpx 上游弃用警告。
- 前端 ESLint/TypeScript：通过；Vitest：1 file、6 tests passed。
- Vite production build：51 modules，JS 250.94 kB（gzip 80.22 kB）。
- 凭据策略：通过。
- 离线演示：生成 8 个确定性 ZIP，成功。

## 另行运行的真实应用验证

主工作区启动 FastAPI 8000 和 Vite 5173 后，执行 `python scripts/demo.py --base-url http://127.0.0.1:5173`：健康检查、上传、完成查询和 Markdown 导出通过。随后用 Playwright + 系统 Edge 走通首页 → 选择 Python 规则 → 上传 `python-pass.zip` → 通过报告 → 历史记录；桌面 1440×1000 和移动 390×844 截图完成，控制台 0 error/warning。

发现并修复了两项集成问题：前后端规则/报告 JSON 形状不一致；缺失 favicon 导致控制台 404。两者均在重新执行前端全门禁和浏览器流程后转绿。

## 未验证项

- 本机没有 Docker CLI，未运行 `docker compose config/build/up/down`，因此不能声称容器冷启动通过。
- 没有远程仓库/registry/云部署权限，未验证 CI 最后一次运行、镜像发布或公网 URL。
- 冷启动使用了本机缓存包；锁文件安装没有下载新版本，但并非物理离线新机器。

提交前必须在具备 Docker 和远程 CI 的环境补做上述三项，并把真实链接/结果更新到本报告。

