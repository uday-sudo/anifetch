{
  python3Packages,
  pkgs,
  ...
}: let
  loop = pkgs.writeShellScriptBin "loop-anifetch.sh" ''
    ${(builtins.readFile ../../loop-anifetch.sh)}
  '';
in
pkgs.stdenv.mkDerivation {
  pname = "anifetch";
  version = "0.1.0";
  
  src = pkgs.runCommand "anifetch-src" {} ''
    mkdir -p $out
    cp ${pkgs.writers.writePython3Bin "anifetch.py" {doCheck = false;} (builtins.readFile ../../anifetch.py)}/bin/anifetch.py $out/anifetch
  '';
  
  nativeBuildInputs = [
    pkgs.makeWrapper
    pkgs.python3
  ];
  
  buildInputs = [
    pkgs.bc
    pkgs.chafa
    pkgs.ffmpeg
    loop
  ];
  
  installPhase = ''
    mkdir -p $out/bin
    cp anifetch $out/bin/anifetch
    chmod +x $out/bin/anifetch
  '';
  
  postFixup = ''
    wrapProgram $out/bin/anifetch \
      --prefix PATH : ${pkgs.lib.makeBinPath [
        pkgs.bc
        pkgs.chafa
        pkgs.ffmpeg
        loop
        pkgs.python3
      ]} \
      --prefix PYTHONPATH : ${pkgs.python3.pkgs.makePythonPath (with pkgs.python3Packages; [
        # List the same Python packages here as in propagatedBuildInputs
      ])}
  '';
}