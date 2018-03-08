% Hao Chen  z5102446
% Project_1 COMP9414
% 2017 s1


% Question_1
% ————————————————————————————————————————————————-----

%if there is an empty list, then return 0.
weird_sum([], 0).

%if the number >=5 then compute the suqare.
weird_sum([Head|Tail],Result) :-
    Head >= 5,
    weird_sum(Tail,Result1),
    Result is Head * Head + Result1.

%if the number =<2 then minus the abs.
weird_sum([Head|Tail],Result) :-
    Head =< 2,
    weird_sum(Tail,Result2),
    Result is Result2 - abs(Head).

%if no match before then pass.
weird_sum([Head|Tail],Result) :-
    Head<5,Head>2,
    weird_sum(Tail,Result).


% Question_2
% ————————————————————————————————————————————————-----

%find ancestors
ancestor(Ancestor,Person) :-
    parent(Ancestor,Person),
    male(Ancestor).

ancestor(Ancestor,Person) :-
    parent(Parent,Person),
    ancestor(Ancestor,Parent),
    male(Parent).

%match same name
% if the Person1 is the ancestor of Person2, then true.
same_name(Person1,Person2) :-
    ancestor(Person1,Person2).

% if the Person2 is the ancestor of Person1, then true.
same_name(Person1,Person2) :-
    ancestor(Person2,Person1).
   
% if the Person1 and Person2 have the same male ancsetor.
same_name(Person1,Person2) :-
    ancestor(Person,Person1),
    ancestor(Person,Person2).


% ————————————————————————————————————————————————-----
% Question_3

% build the sublist using the given number.
build_list(X,Result_List) :-
    Result is log(X),
    Result_List = [X,Result].

% base case.
log_table([],[]).

% main recursive function table.
log_table([Head|Tail],[List|ResultList]) :-
    build_list(Head,List),
    log_table(Tail,ResultList).


% ————————————————————————————————————————————————-----
% Question_4

 %judge whether the number is odd or even.
odd(Num) :-
    integer(Num),
    1 is Num mod 2.

even(Num) :-
    integer(Num),
    0 is Num mod 2.

%judge from the first number, if it is odd, put in L1, and put L2 into the result if L2 is not empty, then clear L2.
paruns_compute([Head|Tail], ResultList, L1, L2) :-
    odd(Head),
    L2 == [],
    paruns_compute(Tail, ResultList, [Head|L1], L2).

paruns_compute([Head|Tail], [L2|ResultList], L1, L2) :-
    odd(Head),
    L2 \= [],
    paruns_compute(Tail, ResultList, [Head|L1], []).

%judge from the first number, if it is even, put in L2, and put L1 into the result if L1 is not empty, then clear L1.
paruns_compute([Head|Tail], ResultList, L1, L2) :-
    even(Head),
    L1 == [],
    paruns_compute(Tail, ResultList, L1, [Head|L2]).

paruns_compute([Head|Tail], [L1|ResultList], L1, L2) :-
    even(Head),
    L1 \= [],
    paruns_compute(Tail, ResultList, [], [Head|L2]).

% put the L1 and L2 in the end of the resultlist if(L1 or L2 not empty).
paruns_compute([], [L1], L1, _) :-
 L1 \= [].

paruns_compute([], [L2], _, L2) :-
 L2 \= [].

% reverse the list
reverse([],Z,Z).

reverse([H|T],Z,Acc) :-
    reverse(T,Z,[H|Acc]).

%reverse the final list since it is like [[X],[X,X,X]]..
paruns_reverse([],[]).

paruns_reverse([Head|Tail],[Rev|Result]) :-
    reverse(Head,Rev,[]),
    paruns_reverse(Tail,Result).

paruns(List,RunList) :-
    paruns_compute(List,Temp_List,[],[]),
    paruns_reverse(Temp_List,RunList).


% ————————————————————————————————————————————————-----
% Question_5

%Base Case，empty on both side.
is_heap(tree(empty,_,empty)).

%Case 1, empty on the right side, then the lfet must bigger than the element.
is_heap(tree(Left,Num,empty)) :-
    Left = tree(_,Number_Left,_),
    Number_Left >= Num,
    is_heap(Left).

%Case 2, empty on the left side, then the right must bigger than the element.
is_heap(tree(empty,Num,Right)) :-
    Right = tree(_,Number_Right,_),
    Number_Right >= Num,
    is_heap(Right).

%Case 3, both left and right must bigger than the element.
is_heap(tree(Left,Num,Right)) :-
    Left = tree(_,Number_Left,_),
    Right = tree(_,Number_Right,_),
    Number_Left >= Num,
    Number_Right >= Num,
    is_heap(Left),
    is_heap(Right).