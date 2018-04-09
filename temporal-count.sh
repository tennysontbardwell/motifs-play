#!/usr/bin/env bash
fun() {
    input=$1
    delta=1200
    output="$input.temporal-count-$delta"

    # words=$(wc $input | cut -d " " -f2)
    # if [ "$words" -lt 500 ]; then
    #     echo Skipping $input word count is $words
    #     return
    # else
    #     echo Word Count is $words
    # fi

    if [ ! -f $output ]; then
        echo Running for $input
        ./snap/examples/temporalmotifs/temporalmotifsmain -i:$input "-o:$output" delta:$delta
    else
        echo Skipping $input
    fi
}
export -f fun

find build/twitter/one_month/ -type f \
    | grep -v 'temporal-count-1200' \
    | xargs -L 1 -P 10 -I {} bash -c 'fun "$@"' _ {}
