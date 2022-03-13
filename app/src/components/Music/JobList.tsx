import { useCallback, useMemo, useState } from 'react';
import { useAtom } from 'jotai';
import { Container, Grid, Header, Icon, Loader, Message, Pagination } from 'semantic-ui-react';
import { jobsAtomState } from '../../state/Music';
import JobCard from './JobCard';
import useWebsocket from '../../hooks/useWebsocket';

const JobList = () => {
	const [page, setPage] = useState(0);
	const [jobsState, setJobsState] = useAtom(jobsAtomState);

	const socketHandler = useCallback(
		(event) => {
			const json = JSON.parse(event.data);
			const type = json.type;
			if (type === 'STARTED') {
				setJobsState([...json.jobs, ...jobsState.data.jobs]);
			} else if (type === 'COMPLETED') {
				const newJobs = [...jobsState.data.jobs];
				const completedJobs = json.jobs.reduce((map: any, job: any) => {
					map[job.id] = job;
					return map;
				}, {});
				newJobs.forEach((job, index) => {
					if (completedJobs[job.id]) {
						newJobs[index] = completedJobs[job.id];
					}
				});
				setJobsState([...newJobs]);
			}
		},
		[jobsState.data.jobs, setJobsState]
	);

	const socketState = useWebsocket('/music/jobs/listen', socketHandler);

	const Jobs = useMemo(() => {
		if (jobsState.loading) {
			return <Loader size="big" active />;
		}

		const jobs = jobsState.data.jobs;
		const PAGE_SIZE = 4;
		const jobs_slice = jobs.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE);

		return (
			<Container>
				<Grid stackable>
					<Grid.Row>
						<Grid.Column>
							{socketState === WebSocket.CLOSED ? (
								<Message negative>
									<Message.Header>Refresh page to get Job Updates</Message.Header>
								</Message>
							) : null}
						</Grid.Column>
					</Grid.Row>
					<Grid.Row>
						<Grid.Column>
							<Container>{jobs.length === 0 ? 'No Existing Jobs' : null}</Container>
						</Grid.Column>
					</Grid.Row>
					<Grid.Row>
						<Grid.Column>
							<Container>
								<Grid stackable stretched>
									{jobs_slice.map((job) => (
										<Grid.Column computer={4} tablet={8} key={job.id}>
											<JobCard job={job} />
										</Grid.Column>
									))}
								</Grid>
							</Container>
						</Grid.Column>
					</Grid.Row>
					<Grid.Row textAlign="center">
						<Grid.Column>
							<Pagination
								boundaryRange={0}
								activePage={page + 1}
								firstItem={null}
								lastItem={null}
								prevItem={{ content: <Icon name="angle left" />, icon: true }}
								nextItem={{ content: <Icon name="angle right" />, icon: true }}
								ellipsisItem={null}
								totalPages={Math.ceil(jobs.length / PAGE_SIZE)}
								onPageChange={(e, data) => {
									if (data.activePage) {
										setPage(Number(data.activePage) - 1);
									}
								}}
							/>
						</Grid.Column>
					</Grid.Row>
				</Grid>
			</Container>
		);
	}, [jobsState.data.jobs, jobsState.loading, page, socketState]);

	return (
		<Container>
			<Grid padded="vertically">
				<Grid.Row>
					<Grid.Column>
						<Header as="h1">Jobs</Header>
					</Grid.Column>
				</Grid.Row>
				<Grid.Row>
					<Grid.Column>{Jobs}</Grid.Column>
				</Grid.Row>
			</Grid>
		</Container>
	);
};

export default JobList;
