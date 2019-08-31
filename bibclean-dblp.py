#!/usr/bin/env python3

import biblib.bib, requests
import sys, re, urllib.parse, collections
from pprint import pprint

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
        try:
          title = ent["title"]
          year = ent["year"]
          oquery = year +" "+ title +" "+ " ".join(i.last for i in ent.authors())
          oquery = re.sub("[^ ]\\\\.", lambda x: x[0][0], oquery)
          oquery = re.sub("\\\\[^{]+?[ {]", lambda x: "", oquery)
          oquery = oquery.replace("{", "").replace("}", "")
          query = oquery.replace(" ", "+")
          query = urllib.parse.quote(query)
          query = query.replace("%2B", "+")
          queries.append((ent, oquery, query))
        except:
          pass

    mode = "bib"
    if mode=="bib":
        #queries = sorted(queries, key=lambda x: x[1])
        for i, (ent, oquery, query) in enumerate(queries):
            print()
            resp = requests.get("https://dblp.org/search/publ/api?format=bib&q=" + query).text
            if resp:
                respbib = biblib.bib.Parser().parse(resp, log_fp=sys.stderr).get_entries()
                if len(respbib) == 1:
                    print("% OK ", oquery)
                    bibl = respbib[0]
                    bibl.key = ent.key
                    print(bibl.to_bib(wrap_width=120))
                    continue
            print("% BAD", oquery)
            print(ent.to_bib(wrap_width=120))

    else:
        fails = []
        succs = {}
        for i, (ent, oquery, query) in enumerate(queries):
            print(i)
            print("=", oquery)
            resp = requests.get("https://dblp.org/search/publ/api?format=json&q=" + query).json()

            if resp and "hit" in resp["result"]["hits"]:
                for hit in resp["result"]["hits"]["hit"]:
                    try:
                        venue = hit["info"].get("venue", hit["info"].get("booktitle", "-"))
                        succs[venue] = succs.get(venue, 0) + 1
                        print("*", hit["info"]["year"] +" "+
                              hit["info"]["authors"]["author"][0].split(" ")[-1] +". "+
                              hit["info"]["title"] +" "+
                              venue)
                    except:
                        pprint(hit["info"])
                        pass
            else:
                fails.append( oquery )
            print()
            print()

        pprint(fails)
        pprint(succs)
        print(len(fails))


if __name__ == '__main__':
    main()
