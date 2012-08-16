import sys
nonalf='[]<>, -'
trans={'A':'ADJ', 'N':'NOUN'}

for line in sys.stdin:
  newLine=''
  l=line.strip('\n')
  for c, char in enumerate(l):
    if char in trans.keys() and (c == len(l)-1 or l[c+1] in nonalf):
      newLine+=trans[char]
    else:
      newLine+=char
  
  
  print newLine  