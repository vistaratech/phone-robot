import { N_JOINTS, RobotState } from './PhoneBotClient';

// Neutral crouch (rad) - same order as robot/config.yaml. Tune for your robot.
export const STAND = [0, 0, 0, -0.4, 0.8, -0.4, 0, 0, 0, -0.4, 0.8, -0.4, 0];

export interface Policy { act(state: RobotState | null, t: number): number[]; }

export class StandPolicy implements Policy {
  act(_s: RobotState | null, _t: number) { return STAND.slice(0, N_JOINTS); }
}

// To run a trained locomotion policy on the phone:
//   npm i onnxruntime-react-native
// then implement Policy.act() using IMU (react-native-sensors) + state.q/dq as
// observations - the observation layout must match your training setup.
