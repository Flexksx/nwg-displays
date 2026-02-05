{
  description = "Modernized nwg-displays with uv and nix";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    flake-parts.url = "github:hercules-ci/flake-parts";
    pyproject-nix = {
      url = "github:pyproject-nix/pyproject.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    uv2nix = {
      url = "github:pyproject-nix/uv2nix";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    pyproject-build-systems = {
      url = "github:pyproject-nix/build-system-pkgs";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.uv2nix.follows = "uv2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs =
    inputs@{
      self,
      flake-parts,
      nixpkgs,
      uv2nix,
      ...
    }:
    flake-parts.lib.mkFlake { inherit inputs; } {
      systems = [
        "x86_64-linux"
        "aarch64-linux"
      ];

      perSystem =
        {
          config,
          pkgs,
          system,
          ...
        }:
        let
          workspace = uv2nix.lib.workspace.loadWorkspace { workspaceRoot = ./.; };
          python = pkgs.python314;

          pythonSet =
            (pkgs.callPackage inputs.pyproject-nix.build.packages {
              inherit python;
            }).overrideScope
              (
                pkgs.lib.composeManyExtensions [
                  inputs.pyproject-build-systems.overlays.default
                  workspace.mkPyprojectOverlay
                  { sourcePreference = "wheel"; }
                  (final: prev: { })
                ]
              );

          runtimeDeps = with pkgs; [
            gtk3
            gtk-layer-shell
            gobject-introspection
            pango
            gdk-pixbuf
            atk
          ];
        in
        {
          packages = rec {
            default = nwg-displays;

            nwg-displays = pkgs.stdenv.mkDerivation {
              pname = "nwg-displays";
              version = "0.1.4";
              src = ./.;

              nativeBuildInputs = [
                pkgs.makeWrapper
                pkgs.wrapGAppsHook
              ];
              buildInputs = runtimeDeps;

              installPhase = ''
                mkdir -p $out/bin
                cp -r ${pythonSet.mkVirtualEnv "nwg-env" workspace.deps.default} $out/venv
                ln -s $out/venv/bin/nwg-displays $out/bin/nwg-displays
              '';

              preFixup = ''
                makeWrapperArgs+=("''${gappsWrapperArgs[@]}")
              '';
            };
          };

          devShells.default = pkgs.mkShell {
            packages =
              with pkgs;
              [
                uv
                python
                pkg-config
              ]
              ++ runtimeDeps;

            shellHook = ''
              export LD_LIBRARY_PATH="${pkgs.lib.makeLibraryPath runtimeDeps}:$LD_LIBRARY_PATH"
              if [ -f "pyproject.toml" ]; then
                uv sync
              fi
            '';
          };
        };
    };
}
