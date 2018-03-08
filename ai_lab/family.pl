% Program:  family.pl
% Source:   Prolog
%
% Purpose:  This is the sample program for the Prolog Lab in COMP9414/9814/3411.
%           It is a simple Prolog program to demonstrate how prolog works.
%           See lab.html for a full description.
%
% History:  Original code by Barry Drake


% parent(Parent, Child)
%
parent(albert, jim).
parent(albert, peter).
parent(jim, brian).
parent(john, darren).
parent(peter, lee).
parent(peter, sandra).
parent(peter, james).
parent(peter, kate).
parent(peter, kyle).
parent(brian, jenny).
parent(irene, jim).
parent(irene, peter).
parent(pat, brian).
parent(pat, darren).
parent(amanda, jenny).

grandparent(Grandparent, Grandchild) :-
    parent(Grandparent, Child),
    parent(Child, Grandchild).


siblings(Child1,Child2) :-
    parent(Parent,Child1),
    parent(Parent,Child2),
    Child1 \= Child2.



%find ancestors.
ancestor(Ancestor,Person) :-
    parent(Ancestor,Person),
    male(Ancestor).

ancestor(Ancestor,Person) :-
    parent(Parent,Person),
    ancestor(Ancestor,Parent),
    male(Parent).

%match same name
same_name(Person1,Person2) :-
    ancestor(Person1,Person2).

same_name(Person1,Person2) :-
    ancestor(Person2,Person1).
    
same_name(Person1,Person2) :-
    ancestor(Person,Person1),
    ancestor(Person,Person2).



% female(Person)
%
female(irene).
female(pat).
female(lee).
female(sandra).
female(jenny).
female(amanda).
female(kate).

% male(Person)
%
male(albert).
male(jim).
male(peter).
male(brian).
male(john).
male(darren).
male(james).
male(kyle).


% yearOfBirth(Person, Year).
%
yearOfBirth(irene, 1923).
yearOfBirth(pat, 1954).
yearOfBirth(lee, 1970).
yearOfBirth(sandra, 1973).
yearOfBirth(jenny, 2004).
yearOfBirth(amanda, 1979).
yearOfBirth(albert, 1926).
yearOfBirth(jim, 1949).
yearOfBirth(peter, 1945).
yearOfBirth(brian, 1974).
yearOfBirth(john, 1955).
yearOfBirth(darren, 1976).
yearOfBirth(james, 1969).
yearOfBirth(kate, 1975).
yearOfBirth(kyle, 1976).

older(Person1, Person2) :-
    yearOfBirth(Person1, Year1),
    yearOfBirth(Person2, Year2),
    Year2 > Year1.


olderBrother(Brother, Person) :-
    siblings(Brother,Person),
    older(Brother,Person),
    male(Brother).


children(Parent,ChildList) :-
    findall(Child,parent(Parent,Child),ChildList).


% deal with the duplicated siblings
siblings_list(Child,NewSiblings) :-
    findall(Person,siblings(Child,Person),Siblings),
    remove_dups(Siblings,NewSiblings).





%Base case
list_Count([],0).

%list count function
list_Count([Head|Tail], Count) :-
    list_Count(Tail,Count2),
    Count is Count2 + 1.





