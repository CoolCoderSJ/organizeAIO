{ pkgs, ... }: {

  # Which nixpkgs channel to use.
  channel = "stable-23.05"; # or "unstable"

  packages = [
    pkgs.python310Full
    pkgs.python310Packages.virtualenv
  ];
}