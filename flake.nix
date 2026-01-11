{
  description = "nwg-displays development environment with uv and GTK";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs =
    {
      self,
      nixpkgs,
      flake-utils,
      ...
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = import nixpkgs { inherit system; };

        runtimeDeps = with pkgs; [
          gtk3
          pango
          gdk-pixbuf
          atk
          glib
          gtk-layer-shell
          gobject-introspection
        ];
      in
      {
        devShells.default = pkgs.mkShell {
          name = "nwg-displays-dev";

          buildInputs =
            with pkgs;
            [
              python312
              uv

              pkg-config
              gcc
            ]
            ++ runtimeDeps;

          shellHook = ''
            export GI_TYPELIB_PATH="${pkgs.lib.makeSearchPath "lib/girepository-1.0" runtimeDeps}"
            export XDG_DATA_DIRS="${pkgs.gsettings-desktop-schemas}/share/gsettings-schemas/${pkgs.gsettings-desktop-schemas.name}:${pkgs.gtk3}/share/gsettings-schemas/${pkgs.gtk3.name}:$XDG_DATA_DIRS"
            export LD_LIBRARY_PATH="${pkgs.lib.makeLibraryPath runtimeDeps}:$LD_LIBRARY_PATH"
          '';
        };
      }
    );
}
