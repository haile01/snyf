# Snyf
Sniffing Snyk's reports on NPM/Maven dependencies

## Why?
- [Redhat Dependency Analysis](https://marketplace.visualstudio.com/items?itemName=redhat.fabric8-analytics) and `npm audit` depends on whether or not the dependencies conflict with each other, while all I want is direct vulns.
- Snyk-ing every dependency manually is ~~mental~~skill issue
- OSV-Scanner can't do with NPM _yet_
- Same for Maven...

## How?
Run the script at the project folder
```
python3 -m snyf.main test
python3 -m snyf.main npm 
python3 -m snyf.main maven <target file> 
```

## That's it?
Yep
