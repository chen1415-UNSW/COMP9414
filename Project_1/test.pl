%Queustion 1 werid_sum

werid_sum([],0).

werid_sum([Head|Tail],Result):-
    Head >= 5,
    werid_sum(Tail,Result1),
    R1 is Head*Head,
    Result is Result1 + R1.

werid_sum([Head|Tail],Result):-
    Head =< 2,
    werid_sum(Tail,Result2),
    R2 is abs(Head),
    Result is Result2 - R2.


werid_sum([Head|Tail],Result):-
    Head < 5, Head >2,
    werid_sum(Tail,Result).

%% %base case
%% weird_sum([], 0).

%% %if the number >=5 then compute the suqare.
%% weird_sum([Head|Tail],Result) :-
%%     Head >= 5,
%%     weird_sum(Tail,Result1),
%%     Result is Head * Head + Result1.

%% %if the number =<2 then minus the abs.
%% weird_sum([Head|Tail],Result) :-
%%     Head =< 2,
%%     weird_sum(Tail,Result2),
%%     Result is Result2 - abs(Head).

%% %if no match before then pass.
%% weird_sum([Head|Tail],Result) :-
%%     Head<5,Head>2,
%%     weird_sum(Tail,Result).
