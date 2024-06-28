# A tweak to the Myers bit-parallel algorithm for finding Levenshtein distance

I have had covid and I was trying to improve my solution for the [levenshtein distance code.golf hole](https://code.golf/levenshtein-distance) 
and I stumbled across [this implementation by Nathan Rooy (dubbed "turboshtein")](https://github.com/nathanrooy/turboshtein/tree/main) of an algorithm by Gene Myers (laid out in [this paper](https://dl.acm.org/doi/pdf/10.1145/316542.316550).)

The way the algorithm works is by taking the iterative method, which stores an array of distances with a length equal to one of the strings, and uses the recurrence relation

```
C[i, j] = min(C[i-1,j]+1, C[i,j-1]+1, C[i-1,j-1]+(0 if s[i]==t[j] else 1))
with C[i,0]=i
```
Where strings are 1-indexed.

Myers' algorithm notices that the difference between `C[i,j]` and `C[i-1,j]` or `C[i,j-1]` is always either 1, 0, or -1, and calculates four bitvectors, two storing negative differences, and two positive, for each direction, vertical and horizontal. So we can calculate column by column, and we know that if the highest bit is set in either horizontal difference, then `C[len(s),j]=C[len(s),j-1]+/-1`, and `C[len(s),0] = len(s)`. The tricky part is the bitmath which calculates these differences.

I primarily golf in python, so after adjusting the C implementation, it started failing on certain test cases, and I assumed I must have screwed it up somewhere. So I downloaded the turboshtein package and saw that it was making the same 'mistakes.' This is implemented as `original_myers` in [levenshtein.py](levenshtein.py)

The algorithm laid out in the paper is actually solving a related problem, namely approximate string matching. The idea is that if you calculate the edit distance at a given index in the string to be less than or equal to a threshold parameter `k`, then the string is sufficiently similar at that point.

I found [this paper by Lars Langner](https://www.mi.fu-berlin.de/en/inf/groups/abi/teaching/theses/master_dipl/langner_bitvector/dipl_thesis_langner.pdf)  which refers to 'local vs global scoring.' It says that in the iterative method, you initialize
```
C[0, j] = 
0 for local scoring (occurences start anywhere)
j for global scoring (occurences start at the first position)
```

This seemed promising, and ultimately turned out to be the issue, as I realized later Myers' paper says that the recurrence relation is "subject to the boundary condition that C[0, j] = 0 for all j." 

But I was led off track by Langner's paper when on page 12 it says

"Nevertheless, different initialization of VP can be used to change between local and global
distance scoring. Setting VP = 1<sup>m</sup> uses local scoring and VP = 10<sup>m‐1</sup> global scoring"

The use of superscripts in this context was new to me (D<sup>n</sup> seems to mean repeat binary digit D n times, with no superscript meaning D<sup>1</sup>), so I thought I had to be doing something wrong, but as far as I can figure this is just a wrong assertion about how to implement global scoring. Langner's paper also suggests an initialization practice for the vector array PEq which seems to reverse the order of the relevant bits, which also appears to produce incorrect results. These differences are implemented as `langner_global_init` and `langner_peq` in [levenshtein.py](levenshtein.py).

I don't mean to rag on this paper, 90% of it is about getting this algorithm to run quickly on the GPU and I didn't read most of that, and these critiques are not ultimately relevant to the goal of the paper. I also could be missing things and making a fool of myself.

What I figured out is to reserve the lowest bit of the bitvectors, so each of the masks for characters in PEq need to be offset 1 bit left. This bit serves the same function as the iterative algorithm 1-indexing the strings and reserving position 0. To make sure that on step j `C[0, j]` is abstractly equal to j, all that needs to be done is to bitwise or `1` with the positive horizontal difference Ph. This makes sure that on every step, +1 is added to the top row. Starting from 0, this counts up with each column index. Of course the top row is never actually stored directly, but this leads to (as far as my limited testing has explored) correct outputs for global Levenshtein distance. This is implemented as `global_myers` in [levenshtein.py](levenshtein.py).

Langner's paper also describes optimizations made by Heikki Hyyrö, I believe in [this paper](http://www.stringology.org/event/2002/p6.html), I only skimmed it. I think one of his goals was to reuse variables, and I think I have improved on that by noticing that Pv and Mh can use the same memory, as can Mv and Ph, they are never needed at the same time, and are used to calculate one another. (obviously my python implementation is a proof of concept.) That's `optimized_hyyro` in [levenshtein.py](levenshtein.py).

I wrote all this down because I can't seem to use this algorithm to get anywhere near few enough characters for code golf, which is a shame, but I wanted to use what I learned for something, and so I wrote it down. Thanks for reading, if anyone ever does!