%是list并且是空集则返回0
%base case
deepListCount([],0).

%r是list而且不是空 则拆开计算
deepListCount([Head|Tail],Count) :-
    deepListCount(Tail,Sum_temp),
    deepListCount(Head,Sum_temp2),
    Count is Sum_temp + Sum_temp2.

%不是list且不是空 则返回1
deepListCount(A,1) :-
    not( A = [_|_] ).
