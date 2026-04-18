# MuTO 開發與維護指南 (Development Guide)

這份文件記錄了 MuTO 專案在開發過程中需要遵守的規範，以及常用的工具指令。

## 1. 程式碼自動排版與語法檢查 (Linting & Formatting)

為了確保團隊的程式碼風格保持絕對一致，減少 Code Review 的摩擦，本專案使用 **[Ruff](https://docs.astral.sh/ruff/)** 作為極速的檢查器 (Linter) 與排版器 (Formatter)。它整合並取代了傳統的 `black`、`isort` 和 `flake8`。

設定檔 (包含字數限制 88 字元、強制使用雙引號) 皆統一配置在根目錄的 `pyproject.toml`。

### 一鍵自動排版與修復指令

在修改完程式碼並準備提交 (Commit) 之前，請務必在專案根目錄下於終端機執行以下一鍵指令：

```bash
uv run ruff check --fix . && uv run ruff format .
```

**指令拆解說明：**

- `uv run ruff check --fix .`：自動修復潛在的語法干擾、移除程式碼中未使用的變數/未使用的 `import`，並將 `import` 排序與分類。
- `uv run ruff format .`：依據配置極速將程式碼重構成一致的斷行、引號與縮排風格。

---

### (建議) 開發者編輯器設定 : VS Code

如果您使用 VS Code 作為開發環境，強烈建議安裝擴充功能 **`Ruff`** (開發者為 charliermarsh / Astral Software)。安裝完畢後，您可以在 `.vscode/settings.json` 加入以下設定，讓編輯器在每次**存檔 (Save)** 時自動幫您執行一鍵排版：

```json
{
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.fixAll": "explicit",
      "source.organizeImports": "explicit"
    }
  }
}
```
