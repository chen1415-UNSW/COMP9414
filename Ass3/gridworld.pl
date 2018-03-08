% gridworld.pl
% Simulates a single agent in the Gridworld where truffles and restaurants appear on
% each cycle at randomly determined locations in the 10x10 grid with probability 0.1

% run a trial of 20 cycles of the BDI interpreter starting with the agent at (0,0)

agent_trial :-
        init,
        agent_trials(0, 20, beliefs(at(5,5),stock(0)), intents([],[]), 0, Score),
        write('Total score: '), writeln(Score), !.


% initial state of the world

init :-
        assert(truffle(0,0,0)),
        retractall(truffle(_,_,_)),
        assert(restaurant(0,0,0)),
        retractall(restaurant(_,_,_)),
        retractall(robot_at(_,_)),
        assert(robot_at(5,5)),
        retractall(robot_stock(_)),
        assert(robot_stock(0)).

% run trials up to N

agent_trials(N, N, _, _, Score, Score) :- !.

agent_trials(N1, N, Beliefs, Intentions, Score, Score2) :-
        N1 < N,
        agent_cycle(N1, Beliefs, Beliefs1, Intentions, Intentions1, S),
        Score1 is Score + S,
        N2 is N1 + 1,
        agent_trials(N2, N, Beliefs1, Intentions1, Score1, Score2).


% the BDI interpretation cycle used by the agent

agent_cycle(N, Beliefs, Beliefs1, Intentions, Intentions3, S) :-
        write('Cycle '), write(N), writeln(':'),
        new_events(3),
        world(World),
        write('    World: '), writeln(World),
        write('    Beliefs: '), writeln(Beliefs),
        percepts(World, Percepts),
        write('    Percepts: '), writeln(Percepts),
        trigger(Percepts, Goals),
        write('    Goals: '), writeln(Goals),
        incorporate_goals(Goals, Beliefs, Intentions, Intentions1),
        write('    Intentions: '), writeln(Intentions1),
        get_action(Beliefs, Intentions1, Intentions2, Action),
        write('    New Intentions: '), writeln(Intentions2),
        write('    Action: '), write(Action),
        execute(Action, S),
        write(' scores '), writeln(S),
        world(World1),
        write('    Updated World: '), writeln(World1),
        observe(Action, Observation),
        write('    Observation: '), writeln(Observation),
        update_beliefs(Observation, Beliefs, Beliefs1),
        write('    Updated Beliefs: '), writeln(Beliefs1),
        update_intentions(Observation, Intentions2, Intentions3),
        write('    Updated Intentions: '), writeln(Intentions3).


% list of truffles and restaurants in the world

world(World) :-
        findall(   truffle(X,Y,S),   truffle(X,Y,S), Truffles),
        findall(restaurant(X,Y,S),restaurant(X,Y,S), Restaurants),
        append(Truffles, Restaurants, World), !.

world([]).

%  each with probability 0.1, a new truffle or restaurant appears in at most M random locations on the 10x10 grid

new_events(0).

new_events(M) :-
        Prob is random(10),
        Prob = 0,
        X is round(random(10)),
        Y is round(random(10)),
        not(truffle(X,Y,_)),      % check no truffle or restaurant at location
        not( restaurant(X,Y,_)), !,
        truffle_or_restaurant(X,Y),
        M1 is M - 1,
        new_events(M1).

new_events(M) :-
        M1 is M - 1,
        new_events(M1).

truffle_or_restaurant(X,Y) :-
        K is round(random(2)),
        K is 0, !,
        S is 1 + round(random(10)),
        write('    Event: truffle value '), write(S), write(' appears at '), write('('), write(X), write(','), write(Y), writeln(')'),
        assert(truffle(X,Y,S)).

truffle_or_restaurant(X,Y) :-
        S is round(random(10)),
        write('    Event: restaurant value '), write(S), write(' appears at '), write('('), write(X), write(','), write(Y), writeln(')'),
        assert(restaurant(X,Y,S)).

% new percepts are restaurants or truffles within a viewing range of 10 of the agent

percepts([], []).

percepts([truffle(X,Y,S)|World], [truffle(X,Y,S)|Percepts]) :-
        robot_at(X1,Y1),
        distance((X,Y), (X1,Y1), D),
        D < 10, !,
        percepts(World, Percepts).

percepts([truffle(_,_,_)|World], Percepts) :-
        percepts(World, Percepts).

percepts([restaurant(X,Y,S)|World], [restaurant(X,Y,S)|Percepts]) :-
        robot_at(X1,Y1),
        distance((X,Y), (X1,Y1), D),
        D < 10, !,
        percepts(World, Percepts).

percepts([restaurant(_,_,_)|World], Percepts) :-
        percepts(World, Percepts).

% applicable actions in a state

applicable(move(X1,Y1)) :-
        robot_at(X,Y),
        distance((X,Y), (X1,Y1), 1).

applicable(move(X,Y)) :-
        robot_at(X,Y).

applicable(sell(X,Y)) :-
        robot_at(X,Y),
        restaurant(X,Y,S),
        robot_stock(T),
        T >= S.

applicable(pick(X,Y)) :-
        robot_at(X,Y),
        truffle(X,Y,_S).

% execute action in the Gridworld -- always successfully!

execute(pick(X,Y), 0) :-
        robot_at(X,Y),
        retract(truffle(X,Y,S)),
        retract(robot_stock(T)),
        T1 is T+S,
        assert(robot_stock(T1)),
        assert(picked(X,Y,S)).

execute(sell(X,Y), S) :-
        robot_at(X,Y),
        retract(restaurant(X,Y,S)),
        retract(robot_stock(T)),
        T1 is T-S,
        assert(robot_stock(T1)),
        assert(sold(X,Y,S)).

execute(move(X,Y), 0) :-
        robot_at(X,Y), ! .

execute(move(X,Y), 0) :-
        retract(robot_at(X1,Y1)),
        distance((X1,Y1), (X,Y), 1),
        assert(robot_at(X,Y)).

% Manhattan distance between two squares

distance((X,Y), (X1,Y1), D) :-
        dif(X, X1, Dx),
        dif(Y, Y1, Dy),
        D is Dx + Dy.

% D is |A - B|
dif(A, B, D) :-
        D is A - B, D >= 0, !.

dif(A, B, D) :-
        D is B - A.


% observe result of action

observe(move(_,_), at(X,Y)) :-
        robot_at(X,Y).

observe(pick(X,Y), picked(X,Y,S)) :-
        retract(picked(X,Y,S)).

observe(sell(X,Y), sold(X,Y,S)) :-
        retract(sold(X,Y,S)).

