import { useMemo, useState } from 'react';
import { Container, Grid, Header, Icon, Loader, Pagination } from 'semantic-ui-react';
import { useJobsQuery } from '../../api';
import JobCard from './JobCard';

const JobList = () => {
	const [page, setPage] = useState(0);

	const jobsStatus = useJobsQuery(null, { refetchOnReconnect: true });

	const Jobs = useMemo(() => {
		if (jobsStatus.isFetching) {
			return <Loader size="big" active />;
		}

		const jobs = jobsStatus.data ? jobsStatus.data.jobs : [];
		const PAGE_SIZE = 5;
		const jobs_slice = jobs.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE);

		return (
			<Container>
				<Grid stackable>
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
	}, [jobsStatus.data, jobsStatus.isFetching, page]);

	return useMemo(
		() => (
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
		),
		[Jobs]
	);
};

export default JobList;
