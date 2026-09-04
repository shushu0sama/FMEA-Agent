package 'AlphaPackage' {
    part def Pump;
    part alphaPump : Pump {
        part alphaInner : Pump;
    }
    part alphaMotor : Pump;
}
package 'BetaPackage' {
    part def Pump;
    part betaPump : Pump;
}
