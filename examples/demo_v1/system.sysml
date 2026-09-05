package 'TypedInsideProbe' {
    part def Pump;
    part def Motor;
    action def Spin;

    part hydraulicPump : Pump {
        action pumpSpin : Spin;
        part motor : Motor {
            action spin : Spin;
        }
    }
}
