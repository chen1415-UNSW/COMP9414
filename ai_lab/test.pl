test(f(A,B,C),D) :-
A = B, C = D.




% remove the duplications
remove_dups([],[]).
remove_dups([First | Rest], NewRest) :-
    member(First, Rest),
    remove_dups(Rest, NewRest).
remove_dups([First | Rest], [First | NewRest]) :-
    not(member(First, Rest)),
    remove_dups(Rest, NewRest).


% find all descendants
descendant_list(Parent,NewList) :-
    findall(Person,descendant(Parent,Person),NewDescendants),
    remove_dups(NewDescendants,NewList).

% find all ancestor
ancestor_list(Child,NewList) :-
    findall(Person,descendant(Person,Child),NewAncestor),
    remove_dups(NewAncestor,NewList).

find_olddest_an(Person,Ans) :-
    ancestor_list(Person,An_List),
    member(Ans,An_List),
    male(Ans),
    not(parent(_,Ans)).
