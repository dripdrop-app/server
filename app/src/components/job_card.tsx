import React from 'react';
import { Card, CardContent, CardMedia, CardActions, Typography, CircularProgress, Button } from '@mui/material';

interface Props {
	jobID: string;
	filename?: string;
	youtubeURL?: string;
	artworkURL?: string;
	title?: string;
	artist?: string;
	album?: string;
	grouping?: string;
	completed: boolean;
}

const Job = (props: Props) => {
	return (
		<Card>
			<CardMedia component="img" height="100px" image={props.artworkURL} alt="artwork" />
			<CardContent>
				<Typography variant="h6">{props.filename || props.youtubeURL}</Typography>
			</CardContent>
			<CardActions>
				{props.completed ? (
					<React.Fragment>
						<Button>Download</Button>
						<Button>Retry</Button>
					</React.Fragment>
				) : (
					<CircularProgress />
				)}
			</CardActions>
		</Card>
	);
};

export default Job;
