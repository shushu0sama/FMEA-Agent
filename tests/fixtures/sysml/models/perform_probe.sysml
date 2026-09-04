package 'PerformProbe' {
	private import ScalarValues::*;

	part def Pump;
	part def Motor;
	action def Spin { in speed : ScalarValues::Real; }

	part hydraulicPump : Pump {
		part motor : Motor {
			perform action spin;
		}
	}

	action spin : Spin;
}
