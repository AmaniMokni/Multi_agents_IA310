i_believe(0).
anis(0).
blardone(0).
resources_available.
iteration(0).
!start.

+!start <-
    .count(values_r(_, _, _, _),TOTAL_RESO);
    +res_tot(TOTAL_RESO);
    !get_resources.


+?best_reso(IR,MU_ANIS,MU_BLARDONE,NI) <-
    -ucb_max(_);
    +ucb_max(-1);
    ?iteration(N);
    
    for(values_r(IR,MU_ANIS,MU_BLARDONE,NI)){
        ?ucb_max(UCB_MAX);
        .min([MU_ANIS,MU_BLARDONE],MIN_RESO);
        .ucb(MIN_RESO,NI,N,UCB);
        if(UCB>UCB_MAX){
            -ucb_max(_);
            +ucb_max(UCB);
            -best_resou(_,_,_,_);
            +best_resou(IR,MU_ANIS,MU_BLARDONE,NI);

        };

    };
    ?best_resou(IR,MU_ANIS,MU_BLARDONE,NI).


+!get_resources: resources_available <-
    ?anis(ANIS_PRED);
    ?blardone(BLARDONE_PRED);
    ?iteration(N);

    
    ?best_reso(IR,MU_ANIS,MU_BLARDONE,NI);
    .collect_ressources(IR);

    ?anis(ANIS_SUIV);
    ?blardone(BLARDONE_SUIV);

    if(ANIS_PRED < ANIS_SUIV){
            MU_ANIS_NV = (MU_ANIS + ANIS_SUIV - ANIS_PRED)/2;
    } 
    else {
        MU_ANIS_NV = 0;
    };

    if(BLARDONE_PRED < BLARDONE_SUIV){
            MU_BLARDONE_NV = (MU_BLARDONE + BLARDONE_SUIV - BLARDONE_PRED)/2;
    }
    else {
        MU_BLARDONE_NV = 0;
    };

    -values_r(IR,_,_,_);
    +values_r(IR,MU_ANIS_NV,MU_BLARDONE_NV,NI+1);

    if((NI+1) mod 10 == 0){
        .broadcast(achieve,values_r_nv(IR,MU_ANIS_NV,MU_BLARDONE_NV,NI+1));
    };


    .iteration_suiv;
    .print("iteration:",N," Region num:",IR," anis:",ANIS_SUIV-ANIS_PRED," bardone:",BLARDONE_SUIV-BLARDONE_PRED);

    .count(values_r(_,0,0,_),COLLECTED_RESO);
    ?res_tot(TOTAL_RES);

    if(COLLECTED_RESO == TOTAL_RES) {
        -resources_available;
    };
    if(resources_available){
        !get_resources;
    }else{
        !affichage;
    }.




+!values_r_nv(IR,MU_ANIS,MU_BLARDONE,NI)[source(S)] <-
    .print("from:",S," Resource:",IR," mu_anis:",MU_ANIS," mu_bardone:",MU_BLARDONE);
    -values_r(IR,_,_,_);
    +values_r(IR,MU_ANIS,MU_BLARDONE,NI).


+!affichage: not resources_available <-
    ?anis(ANIS);
    ?blardone(BLARDONE);
    .print("Resultats finaux: ANIS:",ANIS," BLARDONE:",BLARDONE).
