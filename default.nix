let
  nixpkgs = builtins.fetchTarball {
    url = "https://github.com/NixOS/nixpkgs/archive/f641b66ceb34664f4b92d688916472f843921fd3.tar.gz";
    sha256 = "1hglx3c5qbng9j6bcrb5c2wip2c0qxdylbqm4iz23b2s7h787qsk";
  };
in {
  pkgs ? import nixpkgs {},
  cmakeFlags ? [],
}: let
  lib = pkgs.lib;
  stdenv = pkgs.stdenv;
in stdenv.mkDerivation {
  name = "growt";
  version = "0.1.0";

  inherit cmakeFlags;

  src = lib.cleanSourceWith {
    filter = name: type: !(type == "directory" && baseNameOf name == "build");
    src = lib.cleanSourceWith {
      filter = lib.cleanSourceFilter;
      src = ./.;
    };
  };

  buildInputs = with pkgs; [
    tbb
    folly

    # folly's dependencies
    boost
    jemalloc
    glog
    double-conversion
    fmt
  ];
  nativeBuildInputs = with pkgs; [
    linuxPackages.perf
    cmake
    gcc11
    pkg-config 
  ];
}
