let
  nixpkgs = builtins.fetchTarball {
    url = "https://github.com/NixOS/nixpkgs/archive/f641b66ceb34664f4b92d688916472f843921fd3.tar.gz";
    sha256 = "1hglx3c5qbng9j6bcrb5c2wip2c0qxdylbqm4iz23b2s7h787qsk";
  };
  pkgs = import nixpkgs {
    overlays = [
    ];
  };
in pkgs.mkShell {
  buildInputs = with pkgs; [
    ninja
    cmake
    tbb
    folly

    # folly's dependencies
    boost
    jemalloc
    glog
    double-conversion
    fmt

    # kmer-ht dependencies
    boost
    numactl
    zlib
  ];
  nativeBuildInputs = with pkgs; [
    linuxPackages.perf
    cmake
    gcc11
    python38
    python38Packages.pandas

    pkg-config 
  ];
  NIX_CFLAGS_COMPILE = "-march=native";
}