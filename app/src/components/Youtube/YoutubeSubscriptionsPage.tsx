import { Fragment, useMemo } from 'react';
import { useYoutubeSubscriptionsQuery } from '../../api/youtube';

interface YoutubeSubscriptionsPageProps extends YoutubeSubscriptionBody {
	renderItem: (subscription: YoutubeSubscription, index: number) => JSX.Element;
	renderLoading: () => JSX.Element;
}

const YoutubeSubscriptionsPage = (props: YoutubeSubscriptionsPageProps) => {
	const { renderItem, renderLoading } = props;

	const subscriptionsStatus = useYoutubeSubscriptionsQuery(props);

	const subscriptions = useMemo(
		() =>
			subscriptionsStatus.isSuccess && subscriptionsStatus.currentData
				? subscriptionsStatus.currentData.subscriptions
				: [],
		[subscriptionsStatus.currentData, subscriptionsStatus.isSuccess]
	);

	const LoadingItem = useMemo(() => renderLoading(), [renderLoading]);

	return useMemo(
		() => (
			<Fragment>
				<div style={{ display: subscriptionsStatus.isLoading ? 'contents' : 'none' }}>{LoadingItem}</div>
				{subscriptions.map((subscription, i) => (
					<Fragment key={subscription.channelId}>{renderItem(subscription, i)}</Fragment>
				))}
			</Fragment>
		),
		[LoadingItem, renderItem, subscriptions, subscriptionsStatus.isLoading]
	);
};

export default YoutubeSubscriptionsPage;
