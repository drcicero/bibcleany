#!/usr/bin/env python3

import biblib.bib, requests
import sys, re, urllib.parse, collections
from pprint import pprint

def prosa(ent):
    authors = " ".join(i.first + " " + i.last for i in ent.authors())
    t = ent.get("title", "")

    s = ent.get("series", "")  
    j = ent.get("journal", "")
    v = ent.get("volume", "")
    n = ent.get("number", "")
    b = ent.get("booktitle", "")

    p = ent.get("pages", "")
    y = ent.get("year", "")
    pub = ent.get("publisher", "")
    return "{}, {}. In {}, pp. {}, {}, {}.".format(authors, t, " ".join([s, j, v, n, b]), p, pub, y)

def yearAuthorTitle(ent):
    year = ent["year"]
    author = " ".join(i.last for i in ent.authors())
    title = ent["title"]
    query = year +" "+ author + " " + title
    query = re.sub("[^ ]\\\\.", lambda x: x[0][0], query)
    query = re.sub("\\\\[^{]+?[ {]", lambda x: "", query)
    query = query.replace("{", "").replace("}", "")
    return query

def fmtQuery(query):
    query = query.replace(" ", "+")
    query = urllib.parse.quote(query)
    query = query.replace("%2B", "+")
    return query

def main():
    with open(sys.argv[1]) as f:
      raw = biblib.bib.Parser().parse(f, log_fp=sys.stderr).get_entries()

    db = collections.OrderedDict()
    for i in raw:
      key = i.key.lower()
      if key in db:
        if db[key] != i:
          print("duplicate entry ", i.pos, key, i)
      db[ i.key.lower() ] = i

#    for i in db.values():
#      print(i.to_bib(wrap_width=120))
#      print()

    # Pretty-print entries
    queries = []
    for ent in db.values():
        try:    queries.append((ent, yearAuthorTitle(ent)))
        except: pass
        
    #queries = queries[:10]

    #queries = sorted(queries, key=lambda x: x[1])
    succs = []
    succkeys = {}
    l = len(queries)
    for i, (old, query) in enumerate(queries):
        print(str(i*100 // l).zfill(2), end="% ")
        resp = requests.get("https://dblp.org/search/publ/api?format=bib&q=" + fmtQuery(query)).text
        if not resp:          print("BAD", query); continue
        respbib = biblib.bib.Parser().parse(resp, log_fp=sys.stderr).get_entries()
        if len(respbib) != 1: print("BAD", query); continue
        print("OK ", query)
        new = respbib[0]
        new.key = old.key

        old = old.copy(fields=sorted(old.items(), key=lambda kv: (kv[0] not in new, kv[0])))
        old["author"] = " and ".join(a.pretty() for a in old.authors())
        new = new.copy(fields=sorted(new.items(), key=lambda kv: (kv[0] not in new, kv[0])))
        succs.append((old, query, new))
        succkeys[old.key] = 1

    with open("auto-prev.bib", "w") as f:
      for (old, query, new) in succs:
        f.write(old.to_bib(wrap_width=120) + "\n\n")
    with open("auto.bib", "w") as f:
      for (old, query, new) in succs:
        f.write(new.to_bib(wrap_width=120) + "\n\n")

#    with open("auto-prev.prosa", "w") as f:
#      for (old, query, new) in succs:
#        f.write(new.key + ": " + prosa(old) + "\n")
#    with open("auto.prosa", "w") as f:
#      for (old, query, new) in succs:
#        f.write(new.key + ": " + prosa(new) + "\n")

    with open("auto.txt", "w") as f:
      for (old, query, new) in succs:
        f.write(new.key + " " + fmtQuery(query) + "\n")

    with open("manual.bib", "w") as f:
      for ent in db.values():
        if ent.key not in succkeys:
          f.write(ent.to_bib(wrap_width=120) + "\n\n")

#        resp = requests.get("https://dblp.org/search/publ/api?json=bib&q=" + query).text
#        if resp and "hit" in resp["result"]["hits"]:
#            for hit in resp["result"]["hits"]["hit"]:
#                try:
#                    venue = hit["info"].get("venue", hit["info"].get("booktitle", "-"))
#                    succs[venue] = succs.get(venue, 0) + 1
#                    print("*", hit["info"]["year"] +" "+
#                          hit["info"]["authors"]["author"][0].split(" ")[-1] +". "+
#                          hit["info"]["title"] +" "+
#                          venue)
#                except:
#                    pprint(hit["info"])
#                    pass
#        else:
#            fails.append( query )


if __name__ == '__main__':
    main()
