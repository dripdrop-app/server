import { Box } from '@mui/material';
import { ReactNode } from 'react';

interface ConditionalDisplayProps {
	condition: boolean;
	children: ReactNode;
}

const ConditionalDisplay = (props: ConditionalDisplayProps) => (
	<Box display={props.condition ? 'contents' : 'none'}>{props.children}</Box>
);

export default ConditionalDisplay;
