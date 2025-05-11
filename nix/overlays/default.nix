{
  anifetch = final: _prev: {
    anifetch = import ../packages/anifetch-wrapped.nix final.pkgs;
  };
}
