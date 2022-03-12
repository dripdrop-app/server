import { useMemo } from 'react';
import { Container, Loader, Grid, Icon, Pagination } from 'semantic-ui-react';
import { useRecoilState, useRecoilValueLoadable } from 'recoil';
import YoutubeSubscriptionCard from './YoutubeSubscriptionCard';
import { subscriptionOptionsState, subscriptionsSelector } from '../../state/YoutubeCollections';

const SubscriptionsView = () => {
	const [subscriptionOptions, setSubscriptionOptions] = useRecoilState(subscriptionOptionsState);
	const subscriptions = useRecoilValueLoadable(subscriptionsSelector);

	const Subscriptions = useMemo(() => {
		if (subscriptions.state === 'hasValue') {
			return subscriptions.contents.subscriptions.map((subscription) => (
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
	}, [subscriptions.contents.subscriptions, subscriptions.state]);

	const Paginator = useMemo(() => {
		if (subscriptions.state === 'hasValue') {
			return (
				<Pagination
					boundaryRange={0}
					activePage={subscriptionOptions.page}
					firstItem={null}
					lastItem={null}
					prevItem={{ content: <Icon name="angle left" />, icon: true }}
					nextItem={{ content: <Icon name="angle right" />, icon: true }}
					ellipsisItem={null}
					totalPages={Math.ceil(subscriptions.contents.totalSubscriptions / subscriptionOptions.perPage)}
					onPageChange={(e, data) => {
						if (data.activePage) {
							setSubscriptionOptions({ ...subscriptionOptions, page: Number(data.activePage) });
						}
					}}
				/>
			);
		}
		return null;
	}, [setSubscriptionOptions, subscriptionOptions, subscriptions.contents.totalSubscriptions, subscriptions.state]);

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
