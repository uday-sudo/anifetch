{
  python3Packages,
  pkgs,
  ...
}: let
  loop = pkgs.writeShellScriptBin "loop.sh" ''
    export PATH="${pkgs.bc}/bin:${pkgs.ffmpeg}/bin:$PATH"
    ${(builtins.readFile ../../loop.sh)}
  '';
  anifetch-unwrapped = pkgs.writers.writePython3Bin "anifetch.py" {doCheck = false;} (builtins.readFile ../../anifetch.py);
in
  python3Packages.buildPythonPackage {
    name = "aniftech-wrapped";
    src = anifetch-unwrapped;

    build-system = [
      pkgs.python3Packages.setuptools
    ];

    dependencies = [
      pkgs.chafa
      pkgs.ffmpeg
    ];
    preBuild = ''
      cat > setup.py << EOF
      from setuptools import setup

      setup(
        name='anifetch',
        version='0.1.0',
        scripts=['bin/anifetch.py'],
      )
      EOF
    '';
    postInstall = ''
      cp ${loop}/bin/loop.sh $out/bin/loop.sh
      mv $out/bin/anifetch.py $out/bin/anifetch
    '';
  }
