# Fetch-MAA

从 MAA ([MaaAssistantArknights](https://github.com/MaaAssistantArknights/MaaAssistantArknights)) 的 [release](https://github.com/MaaAssistantArknights/MaaAssistantArknights/releases/) 获取预构建的库文件，并使用 nix 提供的 `autoPatchelfHook` 自动修改可执行文件的依赖使其可以在 nix 环境中运行。

## 使用

以下命令会自动下载最新的 MAA 并输出到 `./MAA` 文件夹：

```bash
nix run github:HumXC/fetch-maa
```

传递参数使其存储到不同的文件夹中或者指定版本：

```bash
nix run github:HumXC/fetch-maa -- ./maa v5.24.2
```
