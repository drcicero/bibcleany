Use like this:

```
$ ../path/to/bibcleany-dblp.py src/bibliography.bib
...
wrote auto-prev.bib
wrote auto.bib
wrote manual.bib
```

Uses dblp to download consistent bib citations based on a 'year name title'-query.
For citations that return one match, put the entry from your file into auto-prev.bib and the version from online into auto.bib,
for citations that could not be matched online, put them into manual.bib.
Now, you can compare auto-prev.bib with auto.bib to see what changed.
For your latex you should either concatenate auto.bib and manual.bib again; or like me, include two bibfiles.
