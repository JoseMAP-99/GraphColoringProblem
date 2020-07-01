
        include "globals.mzn";
        int: e;
        int: n;
        int: m;
        set of int: nodes = 0..m;
        array[1..e, 1..2] of int: edges;
        array[0..n] of var nodes: Des;
        
        constraint forall(i in 1..e)(Des[edges[i,1]] != Des[edges[i,2]]);  
        solve :: int_search(Des, most_constrained, indomain_min) satisfy;