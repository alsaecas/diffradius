import React from 'react';
import {Composition} from 'remotion';
import {DiffRadiusVideo} from './VideoFinal';

export const Root: React.FC = () => (
  <Composition
    id="DiffRadiusFinal"
    component={DiffRadiusVideo}
    durationInFrames={8460}
    fps={30}
    width={1920}
    height={1080}
  />
);
