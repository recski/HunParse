for file in $1/*; do
    f=`basename $file | cut -d'.' -f1`
    echo $f
    nice python src/test_parser.py -b -g grammars/currBest.grammar -s out/$f.edges -t $file > out/$f.tagged 2> log/$f.log &
done
