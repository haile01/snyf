# NPM Snyf
Sniffing Snyk's reports on NPM dependencies

## Why?
- [Redhat Dependency Analysis](https://marketplace.visualstudio.com/items?itemName=redhat.fabric8-analytics) and `npm audit` depends on whether or not the dependencies conflict with each other, while all I want is direct vulns.
- Snyk-ing every dependency manually is ~~mental~~skill issue
- OSV-Scanner can't do with NPM _yet_

## How?
Run the script at the project folder
```
python3 main.py
```

## That's it?
Yep
