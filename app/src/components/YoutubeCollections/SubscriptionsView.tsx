import { useMemo, useReducer } from 'react';
import { Container, Loader, Grid, Icon, Pagination, Segment } from 'semantic-ui-react';
import { useYoutubeSubscriptionsQuery } from '../../api';
import SubscriptionCard from './SubscriptionCard';

const initialState: PageState = {
	page: 1,
	perPage: 50,
};

const reducer = (state = initialState, action: Partial<PageState>) => {
	return { ...state, ...action };
};

const SubscriptionsView = () => {
	const [filterState, filterDispatch] = useReducer(reducer, initialState);
	const subscriptionsStatus = useYoutubeSubscriptionsQuery(filterState);

	const totalSubscriptions = useMemo(
		() => (subscriptionsStatus.data ? subscriptionsStatus.data.totalSubscriptions : 0),
		[subscriptionsStatus.data]
	);

	const Subscriptions = useMemo(() => {
		if (subscriptionsStatus.data && !subscriptionsStatus.isFetching) {
			const { subscriptions } = subscriptionsStatus.data;
			return subscriptions.map((subscription) => (
				<Grid.Column computer={4} tablet={8} key={subscription.id}>
					<SubscriptionCard subscription={subscription} />
				</Grid.Column>
			));
		}
		return (
			<Container style={{ display: 'flex', alignItems: 'center' }}>
				<Loader size="huge" active />
			</Container>
		);
	}, [subscriptionsStatus.data, subscriptionsStatus.isFetching]);

	const Paginator = useMemo(() => {
		if (!subscriptionsStatus.isFetching) {
			return (
				<Pagination
					boundaryRange={0}
					activePage={filterState.page}
					firstItem={null}
					lastItem={null}
					prevItem={{ content: <Icon name="angle left" />, icon: true }}
					nextItem={{ content: <Icon name="angle right" />, icon: true }}
					ellipsisItem={null}
					totalPages={Math.ceil(totalSubscriptions / filterState.perPage)}
					onPageChange={(e, data) => {
						if (data.activePage) {
							filterDispatch({ page: Number(data.activePage) });
						}
					}}
				/>
			);
		}
		return null;
	}, [filterState.page, filterState.perPage, subscriptionsStatus.isFetching, totalSubscriptions]);

	return useMemo(
		() => (
			<Container>
				<Grid stackable padded="vertically">
					<Grid.Row>
						<Grid.Column>
							<Grid stackable stretched>
								{Subscriptions}
							</Grid>
						</Grid.Column>
					</Grid.Row>
					<Grid.Row only="computer tablet">
						<Container as="div" style={{ position: 'fixed', bottom: 0 }}>
							<Grid.Column>
								<Segment>
									<Grid stackable>
										<Grid.Row>
											<Grid.Column textAlign="center">{Paginator}</Grid.Column>
										</Grid.Row>
									</Grid>
								</Segment>
							</Grid.Column>
						</Container>
					</Grid.Row>
					<Grid.Row only="mobile">
						<Grid.Column textAlign="center"></Grid.Column>
					</Grid.Row>
				</Grid>
			</Container>
		),
		[Paginator, Subscriptions]
	);
};

export default SubscriptionsView;
