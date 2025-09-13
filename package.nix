{
  stdenvNoCC,
  pkgs,
}: let
  system = stdenvNoCC.hostPlatform.system;
  deps = "libcpr onnxruntime opencv";
in
  stdenvNoCC.mkDerivation {
    pname = "featch-maa";
    version = "1.0";
    src = ./.;

    buildInputs = with pkgs; [gnutar curl jq];

    installPhase = ''
      mkdir -p $out/bin
      cat > $out/bin/featch-maa <<'EOF'
      #!/usr/bin/env bash
      set -e

      usage() {
        cat <<'USAGE'
      Usage: featch-maa [output-folder] [version]

        output-folder : 生成文件输出目录 (默认: MAA)
        version       : 版本号 (如果未提供, 则从 github 获取最新版本)

      示例:
        featch-maa ./MAA v5.24.2
        featch-maa ./MAA          # 从 github 获取最新版本
        featch-maa                # 输出目录取默认值, 从 github 获取最新版本
      USAGE
        exit 0
      }

      # 支持 -h/--help
      case "$1" in
        -h|--help) usage ;;
      esac

      # 从 github 获取最新的 release
      get_latest_release() {
        payload=$(curl -s https://api.github.com/repos/MaaAssistantArknights/MaaAssistantArknights/releases/latest)

        if [ $? -ne 0 ]; then
          echo "Failed to get latest release"
          exit 1
        fi

        tag=$(echo $payload | jq -r '.tag_name')
        # 返回
        echo $tag
      }

      download_release() {
        system=${system} # system 由 nix 提供
        arch="''${system#*-}-''${system%-*}" # linux-x86_64 -> x86_64-linux

        version=$1
        output=$2
        echo "Downloading MAA $version for $arch to $output"

        echo "https://github.com/MaaAssistantArknights/MaaAssistantArknights/releases/download/$version/MAA-$version-$arch.tar.gz"
        curl -fL -o $output "https://github.com/MaaAssistantArknights/MaaAssistantArknights/releases/download/$version/MAA-$version-$arch.tar.gz"
        if [ $? -ne 0 ]; then
          echo "Download failed"
          exit 1
        fi
      }

      OUTPUT_DIR=''${1:-MAA}
      VERSION=''${2:-none}

      # 如果版本号为空, 则获取最新版本号
      if [ "$VERSION" = "none" ]; then
        VERSION=$(get_latest_release)
      fi
      echo "Output : $OUTPUT_DIR"
      echo "Version: $VERSION"

      # 下载 release
      download_release $VERSION /tmp/maa.tar.gz

      # 解压 release
      mkdir -p $OUTPUT_DIR
      tar -xzf /tmp/maa.tar.gz -C $OUTPUT_DIR --strip-components=1

      rm /tmp/maa.tar.gz

      # Patch All ELF
      maa_libs=$OUTPUT_DIR/*.so*
      nix-shell -p ${deps} autoPatchelfHook --run "autoPatchelf $maa_libs"
      chmod +x $maa_libs
      chmod +x $OUTPUT_DIR/maa
      EOF
      chmod +x $out/bin/featch-maa
    '';
  }
