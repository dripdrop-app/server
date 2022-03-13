import { useMemo } from 'react';
import { Container, Loader, Grid, Icon, Pagination } from 'semantic-ui-react';
import { useAtom } from 'jotai';
import YoutubeSubscriptionCard from './YoutubeSubscriptionCard';
import { youtubeSubscriptionsAtomState } from '../../state/YoutubeCollections';

const SubscriptionsView = () => {
	const [subscriptionsState, setSubscriptionsState] = useAtom(youtubeSubscriptionsAtomState);

	const Subscriptions = useMemo(() => {
		if (!subscriptionsState.loading) {
			const { subscriptions } = subscriptionsState.data;
			return subscriptions.map((subscription) => (
				<Grid.Column computer={4} tablet={8} key={subscription.id}>
					<YoutubeSubscriptionCard subscription={subscription} />
				</Grid.Column>
			));
		}
		return (
			<Container style={{ display: 'flex', alignItems: 'center' }}>
				<Loader size="huge" active />
			</Container>
		);
	}, [subscriptionsState.data, subscriptionsState.loading]);

	const Paginator = useMemo(() => {
		if (!subscriptionsState.loading) {
			return (
				<Pagination
					boundaryRange={0}
					activePage={subscriptionsState.data.page}
					firstItem={null}
					lastItem={null}
					prevItem={{ content: <Icon name="angle left" />, icon: true }}
					nextItem={{ content: <Icon name="angle right" />, icon: true }}
					ellipsisItem={null}
					totalPages={Math.ceil(subscriptionsState.data.totalSubscriptions / subscriptionsState.data.perPage)}
					onPageChange={(e, data) => {
						if (data.activePage) {
							setSubscriptionsState({ perPage: subscriptionsState.data.perPage, page: Number(data.activePage) });
						}
					}}
				/>
			);
		}
		return null;
	}, [
		setSubscriptionsState,
		subscriptionsState.data.page,
		subscriptionsState.data.perPage,
		subscriptionsState.data.totalSubscriptions,
		subscriptionsState.loading,
	]);

	return useMemo(
		() => (
			<Container>
				<Grid stackable stretched padded="vertically">
					{Subscriptions}
				</Grid>
				<Grid>
					<Grid.Column textAlign="center">{Paginator}</Grid.Column>
				</Grid>
			</Container>
		),
		[Paginator, Subscriptions]
	);
};

export default SubscriptionsView;
