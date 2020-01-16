Use like this:

```
$ ../path/to/bibcleany-dblp.py src/bibliography.bib
...
wrote auto-prev.bib
wrote auto.bib
wrote manual.bib
```

Uses dblp to download consistent bib citations based on a 'year name title'-query.
For citations that return one match,
  the tool puts the entry from your file into auto-prev.bib and the cleaned-up version from online into auto.bib,
for citations that could not be matched unambiguously (e.g. returned multipled or no matches),
  the tool puts them into manual.bib.
Now, you can compare auto-prev.bib with auto.bib to see what changed.

```
$ meld auto-prev.bib auto.bib # if you want to check what was cleaned up
```

For your latex you should either concatenate auto.bib and manual.bib again; or like me, include two bibfiles.

```
\bibliography{auto.bib, manual.bib} # you can add multiple bibliographies like this
```

LICENCE
Hereby this tool (bibcleany) shall be available under a MIT licence.
In the folder biblib there is a modified version of https://github.com/aclements/biblib, which is available under a MIT licence.
