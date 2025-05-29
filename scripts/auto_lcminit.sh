enxname=$(ifconfig | grep -B 1 192.168.55 | grep enx | cut -d ':' -f1)

if [ -z "$enxname" ]
then
  enxname=$(ifconfig | grep -B 1 192.168.55 | grep enp | cut -d ':' -f1)
  if [[ -z "$enxname" ]]; then
    enxname=$(ifconfig | grep -B 1 192.168.55 | grep usb | cut -d ':' -f1)
    if [[ -z "$enxname" ]]; then
      enxname=$(ifconfig | grep -B 1 192.168.55 | grep eno | cut -d ':' -f1)
    fi
  fi
fi

echo "Got $enxname"
./config_network_lcm.sh -I  $enxname
