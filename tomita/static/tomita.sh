#!/bin/bash

inotifywait -e close_write -m /tomita/in/ |
while read -r directory events filename; do


if [[ $filename =~ ^\..*$ ]]; then
echo "SKIPPING" $filename
else
cat <<EOF  > /tomita/static/config.proto
encoding "utf8";

TTextMinerConfig {
  Dictionary = "/tomita/static/dic.gzt";
  PrettyOutput = "/tomita/pretty/evaluation.html";
  Input = {
    File = "/tomita/in/$filename";
  }
  Articles = [
    { Name = "sci_names" }
  ]
  PrintRules="rules.txt";
  Facts = [
    { Name = "Person" }
  ]
  Output = {
    File = "/tomita/out/$filename.xml";
    Format = xml;
  }
}
EOF
cat /tomita/static/config.proto >&2
/usr/bin/tomita-parser /tomita/static/config.proto
fi

done
