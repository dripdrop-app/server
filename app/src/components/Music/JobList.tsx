import { useMemo, useState } from 'react';
import { CircularProgress, Stack, Typography, Grid, Button } from '@mui/material';
import { useJobsQuery } from '../../api/music';
import JobCard from './JobCard';
import { useSelector } from 'react-redux';

const JobList = () => {
	const [page, setPage] = useState(1);

	const jobsStatus = useJobsQuery({ page, perPage: 5 }, { refetchOnReconnect: true });

	const jobs = useSelector((state: RootState) => {
		const jobIDs = state.music.jobs.ids;
		return jobIDs.map((id) => state.music.jobs.entities[id]) as Job[];
	});

	const Jobs = useMemo(() => {
		if (jobsStatus.isFetching || jobsStatus.isLoading) {
			return (
				<Stack paddingY={5} direction="row" justifyContent="center">
					<CircularProgress />
				</Stack>
			);
		} else if (jobs.length === 0) {
			return (
				<Stack paddingY={5} direction="row" justifyContent="center">
					No Existing Jobs
				</Stack>
			);
		}
		return (
			<Grid container>
				{jobs.map((job) => (
					<Grid key={job.id} item md={3} sm={6} xs={12} padding={1}>
						<JobCard sx={{ height: '100%' }} job={job} />
					</Grid>
				))}
			</Grid>
		);
	}, [jobs.length, jobsStatus.isFetching, jobsStatus.isLoading, jobs]);

	const JobsDisplay = useMemo(
		() => (
			<Stack paddingY={5} spacing={2}>
				{Jobs}
				<Stack direction="row" justifyContent="center">
					<Button disabled={page === 1}>Prev</Button>
					<Button>{page}</Button>
					<Button disabled={jobs.length !== 5}>Next</Button>
				</Stack>
			</Stack>
		),
		[Jobs, jobsStatus.isFetching, jobsStatus.isLoading, page]
	);

	return useMemo(
		() => (
			<Stack paddingY={2}>
				<Typography variant="h3">Jobs</Typography>
				{JobsDisplay}
			</Stack>
		),
		[JobsDisplay]
	);
};

export default JobList;
